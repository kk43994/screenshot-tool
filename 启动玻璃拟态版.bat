@echo off
chcp 65001 >nul
title 截图助手 - 玻璃拟态版启动器
color 0F

cls
echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║                                                  ║
echo   ║    📸 截图助手 v2.5 - 玻璃拟态版                ║
echo   ║       Glassmorphism Design                       ║
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
    echo   请先安装 Python 3.7 或更高版本
    echo   下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo   [✓] Python 环境正常
echo.

REM 检查依赖
python -c "import tkinter; from PIL import Image; import win32clipboard; import keyboard; import pystray" 2>nul
if errorlevel 1 (
    echo   [!] 缺少依赖库，正在安装...
    echo.
    pip install pillow pywin32 keyboard pystray BlurWindow -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
)

echo   [✓] 依赖检查完成
echo.
echo   正在启动玻璃拟态版...
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   ✨ 玻璃拟态版特色（Glassmorphism）：
echo.
echo   • 💎 真正的玻璃拟态设计
echo   • 🌫️  背景模糊效果 (Backdrop Blur)
echo   • 💫 半透明玻璃质感
echo   • ⚪ 细白色边框
echo   • 🌟 柔和阴影和高光
echo   • 🎨 现代化配色方案
echo   • 🔮 脉冲动画效果
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   ⌨️  全局快捷键：
echo.
echo   • Ctrl+Alt+A      普通截图
echo   • Shift+Win+S     截图并复制路径
echo   • Ctrl+Alt+F      切换悬浮窗
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   💡 设计理念：
echo.
echo   玻璃拟态(Glassmorphism)是2025年最流行的设计趋势
echo   通过半透明、背景模糊、柔和边框营造出玻璃质感
echo   让UI元素仿佛悬浮在空间中，既现代又优雅
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   程序已启动，悬浮窗将出现在屏幕右上角
echo   右键悬浮窗可快速访问功能菜单
echo.
echo   本窗口将在3秒后自动关闭...
echo.

REM 使用 pythonw 启动（无命令行窗口）
start "" pythonw "截图助手-玻璃拟态版.pyw"

REM 如果 pythonw 失败，使用 python 启动
if errorlevel 1 (
    start "" python "截图助手-玻璃拟态版.pyw"
)

timeout /t 3 /nobreak >nul
exit
