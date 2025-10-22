@echo off
title 启动截图助手悬浮窗版
cd /d "%~dp0"

REM 检查依赖
python -c "import tkinter; from PIL import Image; import win32clipboard; import keyboard" 2>nul
if errorlevel 1 (
    echo 正在安装必要的依赖...
    pip install pillow pywin32 keyboard
    echo.
)

REM 使用 pythonw 启动（无命令行窗口）
start "" pythonw "截图助手UI悬浮版.pyw"

REM 如果 pythonw 失败，使用 python 启动
if errorlevel 1 (
    start "" python "截图助手UI悬浮版.pyw"
)

exit
