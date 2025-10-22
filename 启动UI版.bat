@echo off
title 启动截图助手UI
cd /d "%~dp0"

REM 检查依赖
python -c "import tkinter; from PIL import Image; import pyperclip" 2>nul
if errorlevel 1 (
    echo 正在安装必要的依赖...
    pip install pillow pyperclip
    echo.
)

REM 使用 pythonw 启动（无命令行窗口）
start "" pythonw "截图助手UI.pyw"

REM 如果 pythonw 失败，使用 python 启动
if errorlevel 1 (
    start "" python "截图助手UI.pyw"
)

exit