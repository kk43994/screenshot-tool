@echo off
title 启动截图助手UI - 调试模式
cd /d "%~dp0"

echo ==============================
echo 正在检查环境...
echo ==============================
echo.

REM 检查 Python
echo 检查 Python...
python --version
if errorlevel 1 (
    echo [错误] 未找到 Python！
    pause
    exit
)
echo [OK] Python 已安装
echo.

REM 检查依赖
echo 检查依赖库...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [错误] tkinter 未安装
    pause
    exit
)
echo [OK] tkinter

python -c "from PIL import Image" 2>nul
if errorlevel 1 (
    echo [警告] PIL/Pillow 未安装，正在安装...
    pip install pillow
)
echo [OK] Pillow

python -c "import pyperclip" 2>nul
if errorlevel 1 (
    echo [警告] pyperclip 未安装，正在安装...
    pip install pyperclip
)
echo [OK] pyperclip

echo.
echo ==============================
echo 正在启动 UI...
echo ==============================
echo.

REM 直接运行看错误信息
python "截图助手UI.pyw"

echo.
echo ==============================
echo 程序已退出
echo ==============================
pause