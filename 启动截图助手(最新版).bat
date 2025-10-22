@echo off
chcp 65001 >nul
title 截图助手 - 现代版启动器
color 0A

cls
echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║                                                  ║
echo   ║           📸 截图助手 v2.0 - 现代版              ║
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
    pip install pillow pywin32 keyboard pystray -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
)

echo   [✓] 依赖检查完成
echo.
echo   正在启动截图助手（现代版）...
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
echo   ✨ 新功能亮点：
echo.
echo   • 现代化设计语言（2025趋势）
echo   • 清理缓存功能
echo   • 查看历史截图
echo   • 设置界面
echo   • 系统托盘图标
echo   • 右键快捷菜单
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   程序已启动，悬浮窗将出现在屏幕右上角
echo   右键悬浮窗可快速访问功能菜单
echo   系统托盘也有图标，方便随时唤出
echo.
echo   本窗口将在3秒后自动关闭...
echo.

REM 使用 pythonw 启动（无命令行窗口）
start "" pythonw "截图助手-现代版.pyw"

REM 如果 pythonw 失败，使用 python 启动
if errorlevel 1 (
    start "" python "截图助手-现代版.pyw"
)

timeout /t 3 /nobreak >nul
exit
