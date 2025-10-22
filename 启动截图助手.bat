@echo off
chcp 65001 >nul
title 截图助手 - 启动器
color 0A

echo.
echo ╔════════════════════════════════════════════╗
echo ║           截图助手 - 启动器                 ║
echo ╚════════════════════════════════════════════╝
echo.
echo 正在检查环境...
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.7 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [✓] Python 环境正常
echo.

REM 检查依赖
python -c "import tkinter; from PIL import Image; import win32clipboard; import keyboard" 2>nul
if errorlevel 1 (
    echo [!] 缺少依赖库，正在安装...
    echo.
    pip install pillow pywin32 keyboard
    echo.
)

echo [✓] 依赖检查完成
echo.
echo 正在启动截图助手（腾讯风格版）...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  快捷键提示：
echo  • Ctrl+Alt+A      普通截图
echo  • Shift+Win+S     截图并复制路径
echo  • Ctrl+Alt+F      切换悬浮窗
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 程序已启动，悬浮窗将出现在屏幕右上角...
echo 如需关闭本窗口，请直接点击 X
echo.

REM 使用 pythonw 启动（无命令行窗口）
start "" pythonw "截图助手-腾讯风格.pyw"

REM 如果 pythonw 失败，使用 python 启动
if errorlevel 1 (
    start "" python "截图助手-腾讯风格.pyw"
)

timeout /t 3 /nobreak >nul
exit